import { useEffect, useRef } from "react";
import * as THREE from "three";

export function ThreeMissionScene() {
  const host = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = host.current;
    if (!element) return;
    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0x091117, 7, 18);
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 40);
    camera.position.set(0, 5.2, 8.5);
    camera.lookAt(0, 0, 0);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    renderer.setClearColor(0x000000, 0);
    element.appendChild(renderer.domElement);

    const ambient = new THREE.AmbientLight(0x8aa6b5, 1.8);
    const redLight = new THREE.PointLight(0xd31636, 9, 10);
    redLight.position.set(-3, 2, 2);
    const whiteLight = new THREE.PointLight(0xdceaf0, 5, 12);
    whiteLight.position.set(3, 4, -2);
    scene.add(ambient, redLight, whiteLight);

    const grid = new THREE.GridHelper(14, 28, 0x2d4a57, 0x172932);
    grid.position.y = -0.48;
    grid.rotation.x = 0.02;
    scene.add(grid);

    const hub = new THREE.Mesh(
      new THREE.IcosahedronGeometry(0.7, 2),
      new THREE.MeshStandardMaterial({ color: 0xd31636, emissive: 0x5c081b, emissiveIntensity: 1.4, roughness: 0.3, metalness: 0.55 }),
    );
    hub.position.y = 0.2;
    scene.add(hub);

    const nodes: THREE.Mesh[] = [];
    const links: THREE.Line[] = [];
    const nodeMaterial = new THREE.MeshStandardMaterial({ color: 0x70c1d1, emissive: 0x113e4b, emissiveIntensity: 1.4, roughness: 0.35, metalness: 0.7 });
    for (let index = 0; index < 16; index += 1) {
      const angle = (index / 16) * Math.PI * 2;
      const radius = index % 2 === 0 ? 2.25 : 3.15;
      const node = new THREE.Mesh(new THREE.OctahedronGeometry(0.12, 0), nodeMaterial.clone());
      node.position.set(Math.cos(angle) * radius, 0.05 + (index % 3) * 0.08, Math.sin(angle) * radius);
      nodes.push(node);
      scene.add(node);
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([hub.position, node.position]),
        new THREE.LineBasicMaterial({ color: index % 4 === 0 ? 0xd31636 : 0x3d6b76, transparent: true, opacity: 0.52 }),
      );
      links.push(line);
      scene.add(line);
    }

    const scan = new THREE.Mesh(
      new THREE.RingGeometry(1.05, 1.12, 64),
      new THREE.MeshBasicMaterial({ color: 0xff5c75, transparent: true, opacity: 0.85, side: THREE.DoubleSide }),
    );
    scan.rotation.x = -Math.PI / 2;
    scan.position.y = -0.42;
    scene.add(scan);

    const resize = () => {
      const width = Math.max(element.clientWidth, 1);
      const height = Math.max(element.clientHeight, 1);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
    };
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(element);
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const clock = new THREE.Clock();
    let frame = 0;
    const animate = () => {
      const elapsed = clock.getElapsedTime();
      if (!reducedMotion) {
        hub.rotation.y = elapsed * 0.45;
        hub.rotation.x = Math.sin(elapsed * 0.5) * 0.16;
        scan.scale.setScalar(1 + (Math.sin(elapsed * 1.25) + 1) * 0.17);
        nodes.forEach((node, index) => {
          node.position.y = 0.05 + (index % 3) * 0.08 + Math.sin(elapsed * 1.2 + index) * 0.06;
          const material = node.material as THREE.MeshStandardMaterial;
          material.emissiveIntensity = 0.95 + (Math.sin(elapsed * 2.2 + index) + 1) * 0.35;
        });
        camera.position.x = Math.sin(elapsed * 0.12) * 0.35;
        camera.lookAt(0, 0, 0);
      }
      renderer.render(scene, camera);
      frame = requestAnimationFrame(animate);
    };
    animate();
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      renderer.dispose();
      element.removeChild(renderer.domElement);
      [grid, hub, scan, ...nodes, ...links].forEach((object) => {
        object.geometry.dispose();
        const material = object.material;
        if (Array.isArray(material)) material.forEach((entry) => entry.dispose());
        else material.dispose();
      });
    };
  }, []);

  return <div className="mission-scene" ref={host} aria-label="Animasi jaringan monitoring sintetis" role="img" />;
}
